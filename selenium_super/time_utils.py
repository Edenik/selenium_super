from datetime import datetime

class TimeUtils():
    def get_time_stamp(self, date:datetime=None, time_splitter=':', date_splitter='-', between_splitter=' ', show_seconds=False):
        seconds_text = ''
        if show_seconds:
            seconds_text = time_splitter + '%S'
        if date is not None:
            return date.strftime("%d{}%m{}%Y{}%H{}%M{}".format(date_splitter, date_splitter,between_splitter, time_splitter,seconds_text)) 
        return datetime.now().strftime("%d{}%m{}%Y{}%H{}%M{}".format(date_splitter, date_splitter,between_splitter, time_splitter,seconds_text)) 
        
    def get_file_time_stamp(self, date_only=False, hour_only=False, date=None):
            ts = self.get_time_stamp(time_splitter="-",between_splitter="_", date=date)
            
            if hour_only:
                return ts.split('_')[-1]
            elif date_only:
                return ts.split('_')[0]

            return ts