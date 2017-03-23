class Combinator(object):
    def __init__(self):
        pass

    def cut_callback(self, t):
        print('cut_callback', t)
        pass

    def frame_callback(self, t, descr):
        print('frame_callback', t, descr)
        pass
