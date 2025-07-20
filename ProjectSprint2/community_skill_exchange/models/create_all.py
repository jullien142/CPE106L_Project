from community_skill_exchange.database import engine, Base
import community_skill_exchange.models  # Ensure all models are imported

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("All tables created.") 