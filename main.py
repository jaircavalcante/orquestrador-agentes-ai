from app.orquestrador import init_agents, orquestrador


if __name__ == "__main__":
    agents = init_agents()
    protocol_id = "PROTO-20251003-0001"
    result = orquestrador(protocol_id, agents)