import pickle


def save_data(filename, object):
    with open(filename, 'wb') as f:
        pickle.dump(object, f)


def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
