if __name__ == "__main__":
    from app import init_db
    from argparse import ArgumentParser
    import uvicorn

    init_db.init_db_sync()

    parser = ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    if parser.parse_args().dev:
        # 开发模式
        uvicorn.run("app.main:app", host="localhost", http="httptools", reload=False)

    else:
        import sys
        from app import app

        # 生产模式
        uvicorn.run(
            app,
            host="localhost",
            http="httptools",
            loop="uvloop" if sys.platform != "win32" else "auto",
            proxy_headers=True,
            forwarded_allow_ips=["127.0.0.1", "::1"],
            reload=False,
        )
