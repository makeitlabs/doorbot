import time
from datetime import *
from dateutil.relativedelta import *
from dateutil.parser import *
from dateutil.tz import *
import calendar


class Schedule():
    @staticmethod
    def factory(t):
        if t == 'Open':
            return EntryScheduleOpen()
        elif t == 'HobbyistRestricted':
            return EntryScheduleHobbyistRestricted()
        assert 0, 'bad Schedule type %s' % t

    def __init__(self):
        pass

    def isAllowed(self, plan):
        pass
    
    def scheduleDesc(self):
        pass


class EntryScheduleOpen(Schedule):
    def __init__(self):
        pass

    def isAllowed(self, plan):
        return True

    def scheduleDesc(self, t = None):
        return 'All Members Allowed 24/7'

if __name__ == '__main__':
    s = Schedule.factory('entry')

    
        
class EntryScheduleHobbyistRestricted(Schedule):
    def __init__(self):
        pass

    def isAllowed(self, plan):
        if 'pro' in plan:
            return True
        else:
            now = datetime.now()
            return self.isWeekend(now) or not self.isWeeknight(now)

    def scheduleDesc(self, t = None):
        if t is None:
            t = datetime.now()
            
        if self.isWeekend(t):
            return 'Weekend: Hobbyists allowed for %s' % self.weekendTimeRemaining(t)
        elif self.isWeeknight(t):
            return 'Weeknight: Hobbyists allowed for %s' % self.weeknightTimeRemaining(t)
        else:
            return 'Weekday: Pro only, Hobbyists allowed in %s' % self.timeUntilWeeknight(t)

    def timeUntilWeekend(self, t):
        weekendStart = t + relativedelta(hour=18, minute=0, second=0, microseconds=0, weekday=FR)
        return weekendStart - t

    def weekendTimeRemaining(self, t):
        weekendEnd = t + relativedelta(hour=6, minute=0, second=0, microseconds=0, weekday=MO)
        return weekendEnd - t

    def timeUntilWeeknight(self, t):
        weeknightStart = t + relativedelta(hour=18, minute=0, second=0, microseconds=0)
        return weeknightStart - t

    def weeknightTimeRemaining(self, t):
        if t.hour >=18:
            weeknightEnd = t + relativedelta(hour=6, minute=0, second=0, microseconds=0, days=+1)
        else:
            weeknightEnd = t + relativedelta(hour=6, minute=0, second=0, microseconds=0, days=0)
        return weeknightEnd - t
        
    def isWeekend(self, t):
        # weekends defined as Fridays after 6PM through Monday before 6AM
        # monday=0 sunday=6
        return bool((t.weekday() == 4 and t.hour >= 18) or
                    (t.weekday() == 5 or t.weekday() == 6) or
                    (t.weekday() == 0 and t.hour < 6))        

    def isWeeknight(self, t):
        # weeknights defined as Monday-Thursday 6PM-6AM next day
        # monday=0 sunday=6
        return bool((t.weekday() == 0 and t.hour >= 18) or
                    (t.weekday() >= 1 and t.weekday() <= 3 and (t.hour < 6 or t.hour >= 18)) or
                    (t.weekday() == 4 and (t.hour < 6)))

    
    def testWeekend(self, tstr):
        t = parse(tstr)
        isit = self.isWeekend(t)
        print('%s is weekend %s' % (t.ctime(), isit))
        print(self.scheduleDesc(t))
        print()
        return isit
    
    def testWeeknight(self, tstr):
        t = parse(tstr)
        isit = self.isWeeknight(t)
        print('%s is weeknight %s' % (t.ctime(), isit))
        print(self.scheduleDesc(t))
        print()
        return isit
    
    def test(self):
        assert self.testWeekend("2016-02-05 17:59:59") == False, 'Friday before 6pm is not weekend'
        assert self.testWeekend("2016-02-05 18:00:00") == True, 'Friday at 6pm is the weekend'
        assert self.testWeekend("2016-02-05 18:01:00") == True, 'Friday after 6pm is weekend'
        assert self.testWeekend("2016-02-06 00:00:00") == True, 'Saturday any time is weekend'
        assert self.testWeekend("2016-02-07 12:00:00") == True, 'Sunday any time is weekend'
        assert self.testWeekend("2016-02-08 00:00:00") == True, 'Monday morning midnight is weekend'
        assert self.testWeekend("2016-02-08 05:59:59") == True, 'Monday morning before 6am is weekend'
        assert self.testWeekend("2016-02-08 06:00:00") == False, 'Monday morning 6am and after is not weekend'
        assert self.testWeekend("2016-02-08 06:00:01") == False, 'Monday morning 6am and after is not weekend'
        assert self.testWeekend("2016-02-09 11:11:11") == False, 'Tuesday is not weekend'
        assert self.testWeekend("2016-02-10 11:11:11") == False, 'Wednesday is not weekend'
        assert self.testWeekend("2016-02-11 11:11:11") == False, 'Thursday is not weekend'
        
        assert self.testWeeknight("2016-02-05 17:59:59") == False, 'Friday before 6pm is a weekday'
        assert self.testWeeknight("2016-02-05 18:00:00") == False, 'Friday at 6pm is weekend'
        assert self.testWeeknight("2016-02-06 13:00:00") == False, 'Saturday any time is weekend'
        assert self.testWeeknight("2016-02-07 13:00:00") == False, 'Sunday any time is weekend'
        assert self.testWeeknight("2016-02-08 05:59:59") == False, 'Monday morning before 6am still weekend'
        assert self.testWeeknight("2016-02-08 06:00:01") == False, 'Monday morning after 6am is weekday'
        assert self.testWeeknight("2016-02-08 17:59:59") == False, 'Monday before 6PM is weekday'
        assert self.testWeeknight("2016-02-08 18:00:00") == True, 'Monday after 6PM is weeknight'
        assert self.testWeeknight("2016-02-09 00:00:00") == True, 'Tuesday midnight is weeknight'
        assert self.testWeeknight("2016-02-09 05:59:59") == True, 'Tuesday before 6AM is weeknight'
        assert self.testWeeknight("2016-02-09 12:00:00") == False, 'Tuesday noon is weekday'
        assert self.testWeeknight("2016-02-09 17:59:59") == False, 'Tuesday before 6PM is weekday'
        assert self.testWeeknight("2016-02-09 18:00:00") == True, 'Tuesday after 6PM is weeknight'

        assert self.testWeeknight("2016-02-10 00:00:00") == True, 'Wednesday midnight is weeknight'
        assert self.testWeeknight("2016-02-10 05:59:59") == True, 'Wednesday before 6AM is weeknight'
        assert self.testWeeknight("2016-02-10 12:00:00") == False, 'Wednesday noon is weekday'
        assert self.testWeeknight("2016-02-10 17:59:59") == False, 'Wednesday before 6PM is weekday'
        assert self.testWeeknight("2016-02-10 18:00:00") == True, 'Wednesday after 6PM is weeknight'

        assert self.testWeeknight("2016-02-11 00:00:00") == True, 'Thursday midnight is weeknight'
        assert self.testWeeknight("2016-02-11 05:59:59") == True, 'Thursday before 6AM is weeknight'
        assert self.testWeeknight("2016-02-11 12:00:00") == False, 'Thursday noon is weekday'
        assert self.testWeeknight("2016-02-11 17:59:59") == False, 'Thursday before 6PM is weekday'
        assert self.testWeeknight("2016-02-11 18:00:00") == True, 'Thursday after 6PM is weeknight'
        
        assert self.testWeeknight("2016-02-12 00:00:00") == True, 'Friday midnight is weeknight'
        assert self.testWeeknight("2016-02-12 05:59:59") == True, 'Friday before 6AM is weeknight'
        assert self.testWeeknight("2016-02-12 06:00:00") == False, 'Friday after 6AM is weekday'
        
if __name__ == '__main__':
    s = Schedule.factory('entry')
    s.test()
