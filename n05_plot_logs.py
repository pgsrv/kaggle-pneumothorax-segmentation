__author__ = "n01z3"

import random
from glob import glob

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


def get_one_log(filename="sx50/0fold_1.log", separator="Validation DICE score: "):
    if "sxh" in filename:
        filename = filename.replace("sxh101/", "sxh101/sxh101").replace("fold_1", "fold_2")
    with open(filename) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    if "se154" in filename:
        try:
            filename = filename.replace("/se154/", "/se154_p2/")
            with open(filename) as f:
                content2 = f.readlines()
            content += [x.strip() for x in content2]
        except:
            pass

    dices = []
    for row in content:
        if "Val" in row:
            dices.append(float(row.split(separator)[-1]))
    return dices


def plot_with_features(values, name, color=COLORS[0], title=None):
    plt.title(name)
    if title:
        plt.title(title)
    plt.ylim(0.72, 0.88)
    plt.xlim(0, 70)
    plt.grid(True)

    if int(title[0]) % 3 == 0:
        # plt.yticks([])
        plt.ylabel("val dice")

    if int(title[0]) > 5:
        plt.xlabel("epoch")

    mvalue = np.amax(values)
    epoch = values.index(mvalue)
    name = f"{name} max:{mvalue:0.4f} e:{epoch}"
    plt.plot(epoch, mvalue, "or", markersize=9, color=color)

    line1, = plt.plot(values, color=color, label=name)
    plt.grid(True, axis="both")
    return line1


def stage1():
    dices = [get_one_log("logs/stage1/ref_8710.log", separator="Validation loss: ")]
    names = ["ref dice 8710LB sota log"]
    folds_scores = [[] for _ in range(10)]
    net_names = ["sx50", "sx101", "se154", "sxh101"]

    plt.figure(figsize=(15, 15))
    out_string = ""
    for model in net_names:
        mvalues = []
        for fold in range(8):
            tdice = get_one_log(f"logs/stage1/{model}/{fold}fold_1.log", "Validation DICE score: ")
            mvalues.append(np.amax(tdice))
            names.append(f"sx101 fold{fold}")
            folds_scores[fold].append(tdice)
        out_string += f"8folds {model}: {np.mean(mvalues):0.4f}" + "\u00B1" + f"{np.std(mvalues):0.4f}\n"

    print(out_string)
    for fold in range(8):
        plt.subplot(3, 3, 2 + fold)
        fold_lst = folds_scores[fold]
        for z, (values, net_name) in enumerate(zip(fold_lst, net_names)):
            line1 = plot_with_features(values, net_name, COLORS[z], f"{fold} fold")
        plt.legend(handler_map={line1: HandlerLine2D(numpoints=3)}, fontsize="medium", loc=4)
        plt.grid(True)

    plt.subplot(3, 3, 1)
    line1 = plot_with_features(dices[0], f"{out_string}" + "1fold ref", color=COLORS[1], title=names[0])
    plt.legend(handler_map={line1: HandlerLine2D(numpoints=1)}, fontsize="medium", loc=4)
    plt.show()


def stage2():
    folds_scores = [[] for _ in range(8)]
    net_names = ["se154", "sx50p", "sx50"]

    plt.figure(figsize=(15, 15))
    out_string, out_string4 = "", ""
    for model in net_names:
        filenames = sorted(glob(f"logs/stage2/{model}/*log"))
        mvalues = []
        for fold, filename in enumerate(filenames):
            tdice = get_one_log(filename, "Validation DICE score: ")
            print(f"{model} fold{fold} epoch:{len(tdice)}")
            if len(tdice) > 0:
                mvalues.append(np.amax(tdice))
                folds_scores[fold].append(tdice)
        out_string += f"{len(mvalues)}folds|{model}: {np.mean(mvalues):0.4f}" + "\u00B1" + f"{np.std(mvalues):0.4f}\n"
        out_string4 += f"{4}folds|{model}: {np.mean(mvalues[:4]):0.4f}" + "\u00B1" + f"{np.std(mvalues[:4]):0.4f}\n"

    print(out_string)
    print(out_string4)
    for fold in range(8):
        plt.subplot(3, 3, 1 + fold)
        fold_lst = folds_scores[fold]
        for z, (values, net_name) in enumerate(zip(fold_lst, net_names)):
            line1 = plot_with_features(values, net_name, COLORS[z], f"{fold} fold")
        plt.legend(handler_map={line1: HandlerLine2D(numpoints=3)}, fontsize="medium", loc=4)
        plt.grid(True)

    plt.subplot(3, 3, 9)
    for tstring in [out_string, out_string4]:
        for z, value in enumerate(tstring.split("\n")):
            # line1, = plt.plot([0], color='w', label=out_string)
            line1, = plt.plot(0, color=COLORS[z], label=value)
            plt.legend(handler_map={line1: HandlerLine2D(numpoints=1)}, fontsize="medium", loc=5)
            plt.axis("off")

    plt.show()


if __name__ == "__main__":
    # stage1()
    stage2()
