### Main Features

- Support Web Management
- Humidity, Temperature, Pressure on Raspberry PI can be tracked on web page
- Support Creatation of cron job on web page 
- Support Creatation of PushBullet notification plan on web page
- Support scan bluetooth devices by AJAX on web page
- Support greet bluetooth device on web page

# IoT Assignment # 1


[![GitHub issues](https://img.shields.io/github/issues/BestJason/IoT_Assignment1.svg)](https://github.com/BestJason/IoT_Assignment1/issues) [![GitHub forks](https://img.shields.io/github/forks/BestJason/IoT_Assignment1.svg)](https://github.com/BestJason/IoT_Assignment1/network)  [![GitHub stars](https://img.shields.io/github/stars/BestJason/IoT_Assignment1.svg)](https://github.com/BestJason/IoT_Assignment1/stargazers) [![GitHub license](https://img.shields.io/github/license/BestJason/IoT_Assignment1.svg)](https://github.com/BestJason/IoT_Assignment1)




## Support Web Management
- All functions of the system provide web management, including **data** management, **cron job** management, **alarm** management, **bluetooth** management.
- You should run the command as follow to start web service:

```shell
	python3 index.py
```

## Humidity, Temperature, Pressure on Raspberry PI can be tracked on web page
- Humidity, Temperature, Pressure both provide a line graph online view, you can clearly see the curve.
- The data is collected once every minute and will be written to the sqlite3 database.
- The cron job that collects data can be added from the cron job management module.
- Running the command as follow, the environment data will be collected and stored in the database:

```shell
	export FLASK_APP=index.py
	flask get_insert_env_data
```

## Support Creatation of cron job on web page
- In this module, you can add a cron job, you can also view the cron job list.
- When adding a cron job, you need to fill in the execution frequency, execute the command, and comment.
- You can also delete cron job.
- All cron jobs added will add into the system.

## Support Creatation of PushBullet notification plan on web page
- All notification alarm messages are sent using the PushBullet interface.
- You should modify the ACCESS TOKEN in models.py.
- Every 30 seconds, the task will detect if an alarm has been triggered.
- You can add trigger condition on web page.
- You can run the command as follow to listen the task:

```shell
	export FLASK_APP=index.py
	flask enable_alarm
```

## Support scan bluetooth devices by AJAX on web page
- All bluetooth devices around will be detected asynchronously by AJAX.

## Support greet bluetooth device on web page
- You can click greet button to greet specific device.
- Raspberry PI will show current temperature when you greet.

### End
