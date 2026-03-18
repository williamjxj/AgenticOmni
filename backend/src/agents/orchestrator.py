class AgentPipelineOrchestrator:
    def __init__(self, agents):
        self.agents = agents

    def run(self, document):
        data = document
        for agent in self.agents:
            data = agent.process(data)
        return data
