import random
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class MemoryObject:
    id: int
    size: int
    is_reachable: bool
    references: List[int]

class MemoryManager:
    def __init__(self, total_memory: int = 1000):
        self.total_memory = total_memory
        self.used_memory = 0
        self.objects: Dict[int, MemoryObject] = {}
        self.next_id = 1
        self.root_objects: List[int] = []

    def allocate_object(self, size: int) -> bool:
        if self.used_memory + size > self.total_memory:
            return False

        # Create new object
        obj_id = self.next_id
        self.next_id += 1
        
        # Randomly decide if this object is reachable
        is_reachable = random.random() < 0.7  # 70% chance of being reachable
        
        # Create random references to other objects
        references = []
        if self.objects:
            num_refs = random.randint(0, 3)
            for _ in range(num_refs):
                ref_id = random.choice(list(self.objects.keys()))
                references.append(ref_id)

        new_object = MemoryObject(
            id=obj_id,
            size=size,
            is_reachable=is_reachable,
            references=references
        )

        self.objects[obj_id] = new_object
        self.used_memory += size

        # Randomly add to root objects
        if random.random() < 0.3:  # 30% chance of being a root object
            self.root_objects.append(obj_id)

        return True

    def run_garbage_collection(self):
        # Mark phase
        marked = set()
        
        def mark_object(obj_id: int):
            if obj_id in marked:
                return
            marked.add(obj_id)
            obj = self.objects[obj_id]
            for ref in obj.references:
                if ref in self.objects:  # Check if reference exists
                    mark_object(ref)

        # Start marking from root objects
        for root_id in self.root_objects:
            if root_id in self.objects:  # Check if root object exists
                mark_object(root_id)

        # Sweep phase
        objects_to_remove = []
        for obj_id, obj in self.objects.items():
            if obj_id not in marked:
                objects_to_remove.append(obj_id)
                self.used_memory -= obj.size

        # Remove unreachable objects
        for obj_id in objects_to_remove:
            del self.objects[obj_id]
            
        # Update is_reachable flag for remaining objects
        for obj_id, obj in self.objects.items():
            obj.is_reachable = obj_id in marked

    def get_memory_state(self):
        return {
            'total_memory': self.total_memory,
            'used_memory': self.used_memory,
            'objects': self.objects,
            'root_objects': self.root_objects
        } 