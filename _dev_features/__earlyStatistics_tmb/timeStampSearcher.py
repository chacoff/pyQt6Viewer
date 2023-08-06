import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

two_months_ago = datetime.now() - timedelta(days=60)

dire = 'T:\\Defects'
fileTXT = 'older_defects.txt'

for root, dirs, files in os.walk(dire):
    for filename in files:
        archive = os.path.join(root, filename)

        file_time = datetime.fromtimestamp(os.path.getmtime(archive))
        if file_time < two_months_ago:
            with open(fileTXT, 'w') as fi:
                print(archive, file=fi)