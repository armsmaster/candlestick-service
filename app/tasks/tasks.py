from app.tasks.broker import broker


@broker.task(schedule=[{"cron": "* * * * *"}])
async def test_task():
    print("Hello World")
