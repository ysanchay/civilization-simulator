import os
import pickle

BASE_DIR = "brains"
CULTURE_FILE = os.path.join(BASE_DIR, "culture.pkl")


# 🔒 Ensure folder exists
def ensure_dir():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)


# 🧠 SAVE AGENT BRAIN
def save_brain(agent, culture=None):
    ensure_dir()

    path = os.path.join(BASE_DIR, f"{agent.name}.pkl")
    data = {
        "memory": agent.memory,
        "energy": agent.energy,
    }

    with open(path, "wb") as f:
        pickle.dump(data, f)

    if culture:
        save_culture(culture)


# 🧠 LOAD AGENT BRAIN
def load_brain(name):
    path = os.path.join(BASE_DIR, f"{name}.pkl")
    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        data = pickle.load(f)

    from agent import Agent
    agent = Agent(name)
    agent.memory = data["memory"]
    agent.energy = data.get("energy", 60.0)

    return agent


# 🌍 SAVE CULTURE
def save_culture(culture):
    ensure_dir()
    with open(CULTURE_FILE, "wb") as f:
        pickle.dump(culture, f)


# 🌍 LOAD CULTURE
def load_culture():
    if not os.path.exists(CULTURE_FILE):
        return None

    with open(CULTURE_FILE, "rb") as f:
        return pickle.load(f)
