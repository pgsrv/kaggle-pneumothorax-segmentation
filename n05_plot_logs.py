import random

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.legend_handler import HandlerLine2D


def get_spaced_colors2(n):
    r, g, b = [int(random.random() * 256) for _ in range(3)]

    step = 256 / n
    ret = []
    for i in range(n):
        r += step
        g += step
        b += step
        ret.append(((r % 256) / 256, (g % 256) / 256, (b % 256) / 256))
    return ret


random.seed(42)
COLORS = get_spaced_colors2(4)


def get_one_log(filename='logs_dl2/0fold_1.log', separator='Validation DICE score: '):
    with open(filename) as f:
        content = f.readlines()

    content = [x.strip() for x in content]
    dices = []
    for row in content:
        if 'Val' in row:
            dices.append(float(row.split(separator)[-1]))
    return dices


def plot_with_features(values, name, color=COLORS[0], title=None):
    plt.title(name)
    if title:
        plt.title(title)
    plt.ylim(0.7, 0.86)
    plt.xlim(0, 50)
    plt.grid(True)
    # plt.ylabel('val dice')
    # plt.xlabel('epoch')

    mvalue = np.amax(values)
    epoch = values.index(mvalue)
    name = f'{name} max:{mvalue:0.4f} e:{epoch}'
    plt.plot(epoch, mvalue, "or", markersize=9, color=color)

    line1, = plt.plot(values, color=color, label=name)
    plt.grid(True)
    return line1


def main():
    dices = [get_one_log('logs/ref_8710.log', separator='Validation loss: ')]
    names = ['ref dice 8710LB sota log']
    folds_scores = [[] for _ in range(10)]

    mvalues = []
    for fold in range(8):
        tdice = get_one_log(f'logs/logs_dgx/{fold}fold_1.log', 'Validation DICE score: ')
        mvalues.append(np.amax(tdice))
        names.append(f'sx101 fold{fold}')
        folds_scores[fold].append(tdice)
    print(f'sx101 {np.mean(mvalues):0.4f} +- {np.std(mvalues):0.4f}')

    mvalues = []
    for fold in range(6):
        tdice = get_one_log(f'logs/logs_dl2/{fold}fold_1.log', 'Validation DICE score: ')
        mvalues.append(np.amax(tdice))
        names.append(f'sx50 fold{fold}')
        folds_scores[fold].append(tdice)

    for fold in range(6, 8):
        tdice = get_one_log(f'logs/logs_dl6/{fold}fold_1.log', 'Validation DICE score: ')
        mvalues.append(np.amax(tdice))
        names.append(f'sx50 fold{fold}')
        folds_scores[fold].append(tdice)

    print(f'sx50 {np.mean(mvalues):0.4f} +- {np.std(mvalues):0.4f}')

    net_names = ['sx101', 'sx50']

    plt.figure(figsize=(15, 15))
    plt.subplot(3, 3, 1)
    line1 = plot_with_features(dices[0], names[0], color=COLORS[-1])
    plt.legend(handler_map={line1: HandlerLine2D(numpoints=3)}, fontsize='medium', loc=3)

    for fold in range(8):
        plt.subplot(3, 3, 2 + fold)
        fold_lst = folds_scores[fold]
        for z, (values, net_name) in enumerate(zip(fold_lst, net_names)):
            line1 = plot_with_features(values, net_name, COLORS[2 * z], f'{fold} fold')
        plt.legend(handler_map={line1: HandlerLine2D(numpoints=3)}, fontsize='medium', loc=4)
        plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main()