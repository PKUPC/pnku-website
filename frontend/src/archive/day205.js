const DATE_LIST = [
    '1900-01-01',
    '1970-01-01',
    '2000-01-01',
    '2000-03-26',
    '2001-03-25',
    '2002-03-24',
    '2003-03-23',
    '2004-02-29',
    '2005-02-27',
    '2006-03-05',
    '2007-02-25',
    '2008-02-24',
    '2009-02-22',
    '2010-03-07',
    '2011-02-27',
    '2012-02-26',
    '2013-02-24',
    '2014-03-02',
    '2015-02-22',
    '2016-01-01',
    '2016-02-28',
    '2016-10-13',
    '2017-02-26',
    '2017-10-05',
    '2018-03-04',
    '2018-10-10',
    '2019-02-24',
    '2019-10-10',
    '2020-02-09',
    '2020-10-08',
    '2021-04-25',
    '2021-10-07',
    '2022-02-01',
    '2022-03-27',
    '2022-09-08',
    '2022-10-06',
    '2023-01-22',
    '2023-03-12',
    '2023-10-05',
    '2024-01-01',
    '2024-02-10',
    '2024-03-10',
    '2024-06-01',
    '2024-07-01',
    '2024-07-11',
    '2024-07-12',
    '2024-07-13',
    '2024-07-14',
    '2024-07-15',
    '2024-07-16',
    '2024-07-17',
    '2024-07-18',
    '2024-07-19',
    '2024-07-20',
    '2024-07-21',
    '2024-07-22',
    '2024-07-23',
    '2024-07-24',
    '2024-07-25',
    '2024-08-01',
    '2024-09-02',
    '2025-01-01',
    '2025-01-29',
];

function isValidDate(year, month, day) {
    try {
        const date = new Date(year, month - 1, day);
        return date.getFullYear() === year && date.getMonth() === month - 1 && date.getDate() === day;
    } catch (e) {
        return false;
    }
}

function apiCall(year, month, day) {
    if (!isValidDate(year, month, day)) {
        return {
            status: 'error',
            title: 'BAD_REQUEST',
            message: '不合法的日期！请选择 1900-01-01 到 2099-12-31 中的合法日期。',
        };
    }
    if (year < 1900 || year > 2099) {
        return {
            status: 'error',
            title: 'BAD_REQUEST',
            message: '不合法的日期！请选择 1900-01-01 到 2099-12-31 中的合法日期。',
        };
    }

    const targetYear = year;
    const targetMonth = String(month).padStart(2, '0');
    const targetDay = String(day).padStart(2, '0');
    const dateStr = `${targetYear}-${targetMonth}-${targetDay}`;
    let targetDate = DATE_LIST[0];

    for (const x of DATE_LIST) {
        if (dateStr >= x) {
            targetDate = x;
        }
    }

    return {
        status: 'success',
        title: '成功！',
        message: '你来到了新的一天！（也许是旧的？）',
        data: `media/puzzle/day2_05/${targetDate}.webp`,
    };
}

export { apiCall };
