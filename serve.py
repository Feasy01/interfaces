from src.app import app

# configuration = CfgParserJson.parse_cfg(os.path.join(os.getcwd(),'Include/config/conenction.json'))
app = app.app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
