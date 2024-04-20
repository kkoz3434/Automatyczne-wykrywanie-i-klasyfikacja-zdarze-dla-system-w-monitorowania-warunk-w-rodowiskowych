import random

import numpy as np
import pandas as pd


def remove_random_indexes(lst, n):
    # Generate N random indexes to remove
    indexes_to_remove = random.sample(range(len(lst)), n)

    # Remove the selected indexes from the list
    new_arr = np.delete(lst, indexes_to_remove)

    return new_arr


def add_elements_by_scheme(lst, X):
    for _ in range(X):
        # Randomly choose an index from the existing list
        index = random.randint(0, len(lst) - 1)

        # Get the neighboring values
        left_neighbor = lst[index - 1] if index > 0 else lst[0]
        right_neighbor = lst[index + 1] if index < len(lst) - 1 else lst[-1]

        # Calculate the mean of neighboring values
        new_value = (left_neighbor + right_neighbor) / 2

        # Insert the new value at the chosen index
        lst = np.insert(lst, index, new_value)
    return lst

def reshape_data( arr: list, data_length):
    if len(arr) > data_length:
        arr = remove_random_indexes(arr, len(arr) - data_length)
    elif len(arr) < data_length:
        arr = add_elements_by_scheme(arr, data_length - len(arr))

    return arr

def prepare_dataset(labeled_data, column):
    labeled_data = [inner for inner in labeled_data if len(inner[0][column].values) > 80]

    # prepare X values
    X = [inner[0][column].values for inner in labeled_data if len(inner[0][column].values) > 80]
    X = [reshape_data(value, 90) for value in X]

    # prepare y values (labels)
    y = [inner[1].value for inner in labeled_data]

    return X,y




if __name__ == '__main__':
    # Example list
    my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # Number of elements to add
    X = 11

    # Add X elements to the list by scheme
    reshape_data(my_list, X)
    print(my_list)
