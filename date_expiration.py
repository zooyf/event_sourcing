#!/usr/bin/env python
# coding=utf-8
# @Time    : 2019/4/20 14:07
# @Author  : Jason Yu
# @Site    : 
# @File    : date_expiration.py
# @Software: PyCharm

"""
爱奇艺会员有效期截止日期

1. 购买的会员分为 单月 半年 一年
2. 过期时间前后15天内可以续订服务(renew), 超过15天尚未续订的,将视同没有购买过.
3. 续订后,将延长会员的有效期
4. 过期后服务不可用
5. 有试用机制,前3天可以免费试用 且每人只能在购买前试用一次 试用期内只能购买 不能更新

定义事件:

购买 buy
续订 renew
试用 try

输入:

事件序列  amount 3d 1m 6m 1y
[
 {"event": "try", "date": "2019 01-02 12:33:23", "amount": "3d"},
 {"event": "buy", "date": "2019 04-02 12:33:23", "amount": "3m"},
 {"event": "try", "date": "2019 05-02 12:33:23", "amount": "3d"}, # 错误事件不能试用
 {"event": "renew", "date": "2019 07-01 12:33:23", "amount": "1m"},
 {"event": "renew", "date": "2019 10-01 12:33:23", "amount": "1m"}, # 错误事件不能订阅
 {"event": "buy", "date": "2019 10-02 12:33:23", "amount": "1m"},
]


输出:

is_expired 会员是否过期 false true
expired_date 会员过期时间 过期显示为 null
could_renew 是否可以续订
"""
import datetime
import calendar


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    print(year)
    print(sourcedate.year)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.datetime(year, month, day)


def to_date(date):
    return datetime.datetime(date.year, date.month, date.day)


class ParseError(Exception):
    msg = ""


class MemState:
    # is_expired = False
    expired_date = None
    # could_renew = False

    could_try = True

    date_format = "%Y %m-%d %H:%M:%S"

    def calculate(self, event, date, amount):
        try:
            converted_date = datetime.datetime.strptime(date, self.date_format)
        except:
            raise ParseError("Invalid date format. Should be %s" % self.date_format)

        # print(event)
        if event == "try":
            if not self.could_try:
                raise ParseError("Cannot try!")
            # print("try event 2")
            self.could_try = False
        elif event == "buy":
            self.could_try = False
        elif event == "renew":
            if not self.could_renew(converted_date):
                raise ParseError("Cannot renew!")

        else:
            raise ParseError("Event Not Allowed!")

        self.calc_expire(event, converted_date, amount)

        return self.is_expired(), self.show_expired(), self.could_renew(converted_date)

    def is_date_expired(self, date):
        """
        specify if the specific date is expired
        :return: True expired
        """
        if not self.expired_date:
            return True
        return to_date(self.expired_date) < to_date(date)

    def calc_expire(self, event, date, amount):
        if event == "buy" and self.is_date_expired(date):
            expired_date = date
        else:
            expired_date = date if self.is_date_expired(date) else self.expired_date

        num = amount[:-1]
        unit = amount[-1]
        if not num.isdigit():
            raise ParseError('num is not digit')

        num = int(num)
        if unit not in "ymd":
            raise ParseError('unit not in "y m d"')

        if unit == 'y':
            expired_date = datetime.datetime(year=expired_date.year + 1, month=expired_date.month,
                                             day=expired_date.day)
        if unit == 'm':
            expired_date = add_months(expired_date, num)

        if unit == 'd':
            expired_date += datetime.timedelta(days=num)

        self.expired_date = expired_date

    def is_expired(self):
        if not self.expired_date:
            return True
        return datetime.datetime.now() > to_date(self.expired_date)

    def could_renew(self, new_date):
        # print("new_date")
        # print(new_date)
        # print(self.expired_date)
        return (abs((to_date(new_date) - to_date(self.expired_date)).days) < 15) and (not self.could_try)

    def show_expired(self):
        return 'null' if self.is_expired() else self.expired_date


if __name__ == "__main__":
    member = MemState()

    inputs = [
        {"event": "try", "date": "2018 01-02 12:33:23", "amount": "3d"},
        {"event": "buy", "date": "2018 04-02 12:33:23", "amount": "3m"},
        {"event": "try", "date": "2018 05-02 12:33:23", "amount": "3d"},  # 错误事件不能试用
        {"event": "renew", "date": "2018 07-10 12:33:23", "amount": "1m"},
        {"event": "renew", "date": "2018 10-01 12:33:23", "amount": "1m"},  # 错误事件不能订阅
        {"event": "buy", "date": "2018 10-02 12:33:23", "amount": "1y"},
    ]

    print("START")
    for i in inputs:
        print("*" * 20)
        try:
            print("in: %s" % i)
            print("out:")
            print(member.calculate(**i))
        except Exception as e:
            print(e)

    print("Done")
