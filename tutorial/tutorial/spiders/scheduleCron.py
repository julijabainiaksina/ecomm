from crontab import CronTab
import getpass

username = getpass.getuser()
my_cron = CronTab(user=username)

job = my_cron.new(command='python /Users/ashelyliu/Documents/GitHub/ecomm/tutorial/tutorial/tutorial/spiders/writeData.py')
for job in my_cron:
    print job
