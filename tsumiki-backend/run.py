def is_dev_mode() -> bool:
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()
    return args.dev


if __name__ == "__main__":
    import uvicorn
    from app import init_db

    init_db.init_db_sync()

    if is_dev_mode():
        # 开发模式
        uvicorn.run("app.main:app", host="localhost", http="httptools", reload=False)
    else:
        from app import app

        # 生产模式
        uvicorn.run(app, host="localhost", http="httptools", reload=False)
