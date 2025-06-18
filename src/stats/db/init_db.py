from .models import Base
from .database import engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("WorkoutStat table created.")
