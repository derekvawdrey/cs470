from .mlagent import MLAgent
from .pfagent import PFAgent
from .randomagent import RandomAgent

agent_register = {
    "Random Agent": 
    {
        "class": RandomAgent,
        "metadata": {
            "override_delay": False
        }
    },
    "Machine Learning Agent": 
    {
        "class": MLAgent,
        "metadata": {
            "override_delay": True
        }
    },
    "Potential Fields Agent": {
        "class": PFAgent,
        "metadata": {
            "override_delay": False
        }
    }
}