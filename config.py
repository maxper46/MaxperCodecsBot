from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]


@dataclass
class Config:
    tg_bot: TgBot


@dataclass
class DatabaseConfig:
    db_user: str
    db_password: str
    db_name: str
    db_host: str = '127.0.0.1'
    db_port: str = '5432'


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'), admin_ids=list(map(int, env.list('ADMIN_IDS')))))


def database_args(path: str | None = None) -> dict:
    env = Env()
    env.read_env(path)
    db_config = DatabaseConfig(
        db_user=env('DB_USER'),
        db_password=env('DB_PASS'),
        db_name=env('DB_NAME')
    )
    return {'host': db_config.db_host, 'port': db_config.db_port, 'dbname': db_config.db_name,
            'user': db_config.db_user, 'password': db_config.db_password}
