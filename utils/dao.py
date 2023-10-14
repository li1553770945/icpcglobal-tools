from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# 创建数据库引擎和Session
Base = declarative_base()


def init_database():
    engine = create_engine(r'sqlite:///data/icpc.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


# 创建任务模型
class ACTeamRecord(Base):
    __tablename__ = 'ac_teams'

    id = Column(Integer, primary_key=True)
    team_id = Column(String)
    check_ac_time = Column(DateTime, default=datetime.now())
    is_send_to_contestant = Column(Boolean, default=False)
    send_to_contestant_time = Column(DateTime, nullable=True)
    is_send_to_coach = Column(Boolean, default=False)
    send_to_coach_time = Column(DateTime, nullable=True)
    is_ac_on_icpcglobal = Column(Boolean, default=False)
    ac_on_icpcglobal_time = Column(DateTime, nullable=True)


class ErrorRecord(Base):
    __tablename__ = 'error_teams'
    id = Column(Integer, primary_key=True)
    check_id = Column(String)
    team_id = Column(String)
    is_send_to_contestant = Column(Boolean)
    send_to_contestant_time = Column(DateTime, nullable=True)
    is_send_to_coach = Column(Boolean)
    send_to_coach_time = Column(DateTime, nullable=True)
    errors = Column(String)


# 创建数据库表格


if __name__ == "__main__":
    session = init_database()
    new_task = ACTeamRecord(team_id="123456")
    session.add(new_task)
    new_task.is_ac_on_icpcglobal =True
    session.commit()
    task = session.query(ACTeamRecord).first()
    print(task.team_id)
    session.close()
