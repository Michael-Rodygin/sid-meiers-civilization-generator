import pandas as pd
import numpy as np
import random


def random_samples(df1, df2, df3, df4, df5):
    # Mersenne Twister Pseudorandom number generator

    sample_1 = df1.sample(random_state=np.random.RandomState())
    df1.drop(sample_1.index, inplace=True)

    sample_2 = df2.sample(random_state=np.random.RandomState())
    df2.drop(sample_2.index, inplace=True)

    sample_3 = df3.sample(random_state=np.random.RandomState())
    df3.drop(sample_3.index, inplace=True)

    sample_4 = df4.sample(random_state=np.random.RandomState())

    sample_5 = df5.sample(random_state=np.random.RandomState())
    df5.drop(sample_5.index, inplace=True)

    frames = [sample_1, sample_2, sample_3, sample_4, sample_5]
    result = pd.concat(frames)

    return result


def styling(df):
    df.index = ['Бонус 1: ', 'Бонус 2: ', 'Бонус 3: ', 'Технология: ', 'Нация: ']
    df.drop(columns='tier', inplace=True)

    return df


def random_distribution(df1, df2, df3, df4, df5):
    if len(df1) < 1 or len(df2) < 1 or len(df3) < 1 or len(df5) < 1:
        return None

    df_player = random_samples(df1, df2, df3, df4, df5)
    df_player = styling(df_player)

    return df_player


def percent(value):
    value = value * 100

    return str(round(value)) + '%'


def shuffle_slice(arr):
    copy = arr[1:]
    random.shuffle(copy)
    arr[1:] = copy

    return arr


def player_seating(players):
    data = {
        '0': ['1', '2', '3', '4'],
        '  ': ['', players[1], '', ''],
        '   ': [(players[4] if len(players) == 5 else ''), ' ', ' ', (players[3] if len(players) > 3 else '')],
        '    ': [players[2], ' ', ' ', players[0]],
    }

    df = pd.DataFrame(data).set_index('0')

    return df


def find_odds(df1, df2, df3, df4, players):
    arr1 = np.array(
        [sum(df1['cul'].tolist()), sum(df1['eco'].tolist()), sum(df1['war'].tolist()), sum(df1['tech'].tolist())])
    arr2 = np.array(
        [sum(df2['cul'].tolist()), sum(df2['eco'].tolist()), sum(df2['war'].tolist()), sum(df2['tech'].tolist())])
    arr3 = np.array(
        [sum(df3['cul'].tolist()), sum(df3['eco'].tolist()), sum(df3['war'].tolist()), sum(df3['tech'].tolist())])
    arr4 = np.array(
        [sum(df4['cul'].tolist()), sum(df4['eco'].tolist()), sum(df4['war'].tolist()), sum(df4['tech'].tolist())])

    cul = arr1[0] + arr2[0] + arr3[0] + arr4[0]
    eco = arr1[1] + arr2[1] + arr3[1] + arr4[1]
    war = arr1[2] + arr2[2] + arr3[2] + arr4[2]
    tech = arr1[3] + arr2[3] + arr3[3] + arr4[3]

    player1 = np.array(
        [percent(arr1[0] / cul), percent(arr1[1] / eco), percent(arr1[2] / war), percent(arr1[3] / tech)])
    player2 = np.array(
        [percent(arr2[0] / cul), percent(arr2[1] / eco), percent(arr2[2] / war), percent(arr2[3] / tech)])
    player3 = np.array(
        [percent(arr3[0] / cul), percent(arr3[1] / eco), percent(arr3[2] / war), percent(arr3[3] / tech)])
    player4 = np.array(
        [percent(arr3[0] / cul), percent(arr3[1] / eco), percent(arr3[2] / war), percent(arr3[3] / tech)])

    dict_all = {
        'Вид победы': ['Культура', 'Экономика', 'Война', 'Технологии'],
        players[0]: player1,
        players[1]: player2,
        players[2]: player3,
        players[3]: player4
    }

    df = pd.DataFrame(dict_all).set_index('Вид победы')

    arr1 = np.array([arr1[0] * 1.1, arr1[1] * 1.05, arr1[2] * 0.95, arr1[3] * 1.05])
    arr2 = np.array([arr2[0] * 1.1, arr2[1] * 1.05, arr2[2] * 0.95, arr2[3] * 1.05])
    arr3 = np.array([arr3[0] * 1.1, arr3[1] * 1.05, arr3[2] * 0.95, arr3[3] * 1.05])
    arr4 = np.array([arr4[0] * 1.1, arr4[1] * 1.05, arr4[2] * 0.95, arr4[3] * 1.05])

    dict_winner = {
        'Вид победы': ['Культура', 'Экономика', 'Война', 'Технологии'],
        players[0]: arr1,
        players[1]: arr2,
        players[2]: arr3,
        players[3]: arr4
    }

    winners = pd.DataFrame(dict_winner).set_index('Вид победы')

    # print("-----------------------------")
    # print(winners)

    win = ['Культурная', 'Экономическая', 'Военная', 'Технологическая']

    arr1 = np.array([(arr1[i], win[i], players[0]) for i in range(len(arr1))])
    arr2 = np.array([(arr2[i], win[i], players[1]) for i in range(len(arr2))])
    arr3 = np.array([(arr3[i], win[i], players[2]) for i in range(len(arr3))])
    arr4 = np.array([(arr4[i], win[i], players[3]) for i in range(len(arr4))])

    matrix = np.array([
        max(arr1, key=lambda x: float(x[0])),
        max(arr2, key=lambda x: float(x[0])),
        max(arr3, key=lambda x: float(x[0])),
        max(arr4, key=lambda x: float(x[0]))
    ])

    matrix = matrix[matrix[:, 0].argsort()[::-1]]

    summ = float(matrix[0][0]) + float(matrix[1][0]) + float(matrix[2][0]) + float(matrix[3][0])

    for el in matrix:
        el[0] = percent(float(el[0]) / summ)

    return df, matrix
