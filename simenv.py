import simpy

env = simpy.Environment()


def get_env():
    global env
    return env
