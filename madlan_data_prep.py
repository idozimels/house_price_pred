# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import datetime
import re

# excel_file = 'https://github.com/idozimels/house_price_pred/raw/main/output_all_students_Train_v10.xlsx'
# data = pd.read_excel(excel_file)
excel_file = 'https://github.com/idozimels/house_price_pred/raw/main/output_all_students_Train_v10.xlsx'
df = pd.read_excel(excel_file, engine='openpyxl')

def prepare_data(df):

    df = df[df['price'].apply(lambda x: bool(re.findall(r'\d+\.?\d*', str(x))))]
    df['price'] = df['price'].apply(lambda x: ''.join(re.findall
                                                      (r'\d+\.?\d*', str(x))) if bool(re.findall(r'\d+\.?\d*', str(x))) else np.nan).astype(float)
    df.reset_index(drop=True, inplace=True)
    # index_to_replace = df[df['price'] == 395000010.00].index
    # df.loc[index_to_replace, 'price'] = 3950000

    df['Area'] = df['Area'].replace("עסקאות באיזור (1000)", "")
    df['Area'] = df['Area'].apply(lambda x: re.findall(r'\d+\.?\d*', str(x)))
    df['Area'] = df['Area'].apply(lambda x: ''.join(x) if len(x) > 0 else np.nan).astype(float)

    columns_to_clean = ['Street', 'city_area', 'description ']
    for column in columns_to_clean:
        df[column] = df[column].str.replace('[,\\.]', '', regex=True)

    valid_types = ['בית פרטי', 'דו משפחתי', 'דופלקס', 'דירה', 'דירת גג', 'דירת גן', 'פנטהאוז', 'קוטג', 'קוטג\'']
    df = df[df['type'].isin(valid_types)]
    df['type'] = df['type'].replace({'קוטג': 'בית פרטי', 'קוטג\'': 'בית פרטי'})
    df['type'] = df['type'].replace('דירת גג', 'פנטהאוז')
    df['floor'] = df['floor_out_of'].str.extract(r'(\d+)', expand=False).astype('Int64')
    df['total_floors'] = df['floor_out_of'].str.extract(r'(?:מתוך|תוך) (\d+)', expand=False).astype('Int64')
    df['floor_out_of'] = df['floor_out_of'].fillna('')
    df.loc[df['floor_out_of'].str.contains('קומת קרקע'), ['floor', 'total_floors']] = 1, 1
    df.loc[df['floor_out_of'].str.contains('קומת מרתף'), 'floor'] = -1
    df.loc[df['floor_out_of'].str.contains(r'קומת קרקע מתוך (\d+)', na=False), 'total_floors'] = df['floor_out_of'].str.extract(r'קומת קרקע מתוך (\d+)', expand=False).astype('Int64')
    df['total_floors'] = df['total_floors'].fillna(df['floor']).astype('Int64')
    conditions = df['type'].isin(['דו משפחתי', 'דירת גן','בית פרטי'])
    df.loc[conditions, ['floor', 'total_floors']] = 1, 1
    conditions2 = (df['type'] == 'פנטהאוז') | (df['type'] == 'דירת גג')
    df.loc[conditions2, 'floor'] = df.loc[conditions2, 'total_floors']
    df = df.dropna(subset=['floor'])
    df['floor'] = df['floor'].astype(int)
    df['total_floors'] = df['total_floors'].astype(int)

    current_date = datetime.datetime.now()

    def calculate_month_difference(date_str):
        try:
            if isinstance(date_str, datetime.datetime):
                date_str = date_str.strftime('%Y-%m-%d %H:%M')
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            month_difference = (date - current_date).days // 30
            if month_difference < 6:
                return 'less_than_6 months'
            elif 6 < month_difference <= 12:
                return 'months_6_12'
            else:
                return 'above_year'
        except ValueError:
            if date_str == 'גמיש':
                return 'flexible'
            if date_str == 'גמיש ':
                return 'flexible'
            elif date_str == 'לא צויין':
                return 'not_defined'
            elif date_str == 'מיידי':
                return 'less_than_6 months'
            else:
                return date_str
    df['entranceDate '] = df['entranceDate '].apply(lambda x: calculate_month_difference(x))

    elevator_mapping = {
        True: 1,
        False: 0,
        'כן': 1,
        'לא': 0,
        'יש': 1,
        'אין': 0,
        'יש מעלית': 1,
        'אין מעלית': 0,
        'yes': 1,
        'no': 0
    }
    parking_mapping = {
        True: 1,
        False: 0,
        'כן': 1,
        'לא': 0,
        'יש': 1,
        'אין': 0,
        'יש חנייה': 1,
        'יש חניה': 1,
        'אין חניה': 0,
        'yes': 1,
        'no': 0
    }
    bars_mapping = {
        True: 1,
        False: 0,
        'כן': 1,
        'לא': 0,
        'יש': 1,
        'אין': 0,
        'יש סורגים': 1,
        'אין סורגים': 0,
        'yes': 1,
        'no': 0,
        np.nan: 0
    }
    storage_mapping = {
        True: 1,
        False: 0,
        'כן': 1,
        'לא': 0,
        'יש': 1,
        'אין': 0,
        'יש מחסן': 1,
        'אין מחסן': 0,
        'yes': 1,
        'no': 0
    }
    air_condition_mapping = {
        True: 1,
        False: 0,
        'כן': 1,
        'לא': 0,
        'יש': 1,
        'אין': 0,
        'יש מיזוג אויר': 1,
        'יש מיזוג אוויר': 1,
        'אין מיזוג אוויר': 0,
        'אין מיזוג אויר': 0,
        'yes': 1,
        'no': 0
    }
    balcony_mapping = {
        True: 1,
        False: 0,
        'כן': 1,
        'לא': 0,
        'יש': 1,
        'אין': 0,
        'יש מרפסת': 1,
        'אין מרפסת': 0,
        'yes': 1,
        'no': 0
    }
    mamad_mapping = {
        True: 1,
        False: 0,
        'כן': 1,
        'לא': 0,
        'יש': 1,
        'אין': 0,
        'יש ממ״ד': 1,
        'יש ממ"ד': 1,
        'אין ממ"ד': 0,
        'אין ממ״ד': 0,
        'yes': 1,
        'no': 0
    }
    handicap_mapping = {
        True: 1,
        False: 0,
        'כן': 1,
        'לא': 0,
        'נגיש לנכים': 1,
        'לא נגיש לנכים': 0,
        'נגיש': 1,
        'לא נגיש': 0
    }

    boolean_columns = ['hasElevator ', 'hasParking ', 'hasBars ', 'hasStorage ', 'hasAirCondition ',
                      'hasBalcony ', 'hasMamad ', 'handicapFriendly ']
    mapping_dict = {
        'hasElevator ': elevator_mapping,
        'hasParking ': parking_mapping,
        'hasBars ': bars_mapping,
        'hasStorage ': storage_mapping,
        'hasAirCondition ': air_condition_mapping,
        'hasBalcony ': balcony_mapping,
        'hasMamad ': mamad_mapping,
        'handicapFriendly ': handicap_mapping}

    for column in boolean_columns:
        df[column] = df[column].map(mapping_dict[column]).fillna(df[column])
    columns_to_convert = ['hasAirCondition ', 'hasParking ', 'hasMamad ']
    df[columns_to_convert] = df[columns_to_convert].astype(int)

    df['City'] = df['City'].str.lstrip()
    df['City'] = df['City'].str.replace('יי', 'י')

    condition_mapping = {
       'לא צויין': 'לא צויין',
       'None': 'לא צויין',
       False: 'לא צויין',
       np.nan: 'לא צויין',
       'שמור': 'שמור',
        'חדש': 'חדש',
        'משופץ': 'משופץ',
        'ישן': 'ישן',
       'דורש שיפוץ': 'ישן'
    }
    df['condition '] = df['condition '].replace(condition_mapping)

    df['room_number'] = df['room_number'].apply(lambda x: float(x) if isinstance(x, (int, float))
        else pd.to_numeric(x.split()[0], errors='coerce'))
    median_room_numbers = df.groupby(pd.cut(df['Area'], bins=5))['room_number'].median()
    df['room_number'] = df.apply(lambda row: median_room_numbers[row['Area']] if pd.isna(row['room_number'])
        else row['room_number'], axis=1)

    average_area = df.groupby('room_number')['Area'].transform('mean')
    average_area = average_area.apply(lambda x: np.ceil(x) if pd.notnull(x) else np.nan).astype('Int64')
    df['Area'] = df['Area'].fillna(average_area)

    df = df.drop(['Street', 'number_in_street', 'city_area', 'num_of_images', 'floor_out_of', 'furniture ',
                 'publishedDays ', 'entranceDate ', 'description '], axis=1)
    return df

# df = prepare_data(df)
