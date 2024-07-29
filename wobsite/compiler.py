# A compiler has a list of targets
# Targets transform an input object into an output object
# The output object is passed to the target's parent
# A target can have multiple children if its input object is a list or dataclass
# If a target outputs None, then it cannot be a child of any other target
# During compilation, resolving None targets automatically calls their child targets to generate input objects

class Target:
    pass