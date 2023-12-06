from src.app import app

# configuration = CfgParserJson.parse_cfg(os.path.join(os.getcwd(),'Include/config/conenction.json'))
app = app.app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
