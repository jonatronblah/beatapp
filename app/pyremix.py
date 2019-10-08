import librosa
import pandas as pd
from pippi import dsp
from itertools import tee, count, chain, islice
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import random


song2 = r"C:\Users\jonathan\Desktop\422-beatslice\app\source\Max D - Many Any - 09 Cuz Its The Way.wav"

song1 = r"C:\Users\jonathan\Desktop\422-beatslice\app\source\04. The Sun Don't Lie.wav"

nclusters = 8

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def getstats(beatpairs, y, sr):
    flatness_list = []
    rms_list = []
    specbw_list = []
    mfcc_list = []
    start = []
    end = []
    note_list = []
    idx = []
    for e, i in enumerate(beatpairs):
        flatness = librosa.feature.spectral_flatness(y=y[i[0]:i[1]])
        flatness = np.mean(flatness)
        rms = librosa.feature.rms(y=y[i[0]:i[1]])
        rms = np.mean(rms)
        specbw = librosa.feature.spectral_bandwidth(y=y[i[0]:i[1]], sr=sr)
        specbw = np.mean(specbw)
        mfcc = librosa.feature.mfcc(y[i[0]:i[1]], sr=sr)
        mfcc = np.mean(mfcc.flatten())
        chroma = librosa.feature.chroma_stft(y[i[0]:i[1]], sr=sr)
        note = np.max([np.mean(i) for i in chroma])
        flatness_list.append(flatness)
        rms_list.append(rms)
        specbw_list.append(specbw)
        mfcc_list.append(mfcc)
        note_list.append(note)
        start.append((i[0])
        end.append(i[1])
        idx.append(e)
    df = pd.DataFrame()
    df['flatness'] = flatness_list
    df['rms'] = rms_list
    df['specbw'] = specbw_list
    df['mfcc'] = mfcc_list
    df['note'] = note_list
    df['start'] = start
    df['end'] = end
    df['idx'] = idx
    X_scaled = StandardScaler().fit_transform(df.iloc[:,:4])
    ky = KMeans(n_clusters=nclusters).fit_predict(X_scaled)
    df['labels'] = ky
    return df
    



def dub(df1, df2, audio):
    out = dsp.buffer()
    dubhead = 0
    for e, i in enumerate(df2.labels[:1200]):
        rpool = list(df1['startstop'][df1['labels'] == i])
        try:
            sl = random.choice(rpool)
        except:
            print(i)
        if audio[sl[0]:sl[1]+int((sl[1]-sl[0])/2)]:
            a = audio[sl[0]:sl[1]+int((sl[1]-sl[0])/2)]
        else:
            a = audio[sl[0]:sl[1]]
        out.dub(a, dubhead)
        dubhead += librosa.samples_to_time((sl[1]-sl[0]), sr=44100)
        print("done dubbing number " + str(e) + " of " + str(len(df2.labels)))
    return out
    


def halftime(b):
    midpoints = []
    b = list(b)
    for e, i in enumerate(b):
        if e < len(b)-1:
            midpoints.append(np.round((i+b[e+1])/2))
        c = midpoints + b
        c.sort()
        c = np.asarray(c, dtype=np.int32)
    return c
    
    
class Track:

    def __init__(self, audio):
        self.audio = dsp.read(audio)
        self.y, self.sr = librosa.load(audio, sr=44100)
        self._, self.beats = librosa.beat.beat_track(y=self.y, sr=self.sr, units='samples')
        self.beatpairs = [i for i in pairwise(self.beats)]
        self.halfbeats = halftime(self.beats)
        self.halfbeatpairs = [i for i in pairwise(self.halfbeats)]
        #self.quarterbeats = halftime(self.halfbeats)
        #self.quarterbeatpairs = [i for i in pairwise(self.quarterbeats)]
        #self.eighthbeats = halftime(self.quarterbeats)
        #self.eighthbeatpairs = [i for i in pairwise(self.eighthbeats)]


track1 = Track(song1)
print("track 1 compiled")

track2 = Track(song2)
print("track 2 compiled")

track1Stats = getstats(track1.halfbeatpairs, track1.y, track1.sr)
print("track 1 stats compiled")
track2Stats = getstats(track2.halfbeatpairs, track2.y, track2.sr)
print("track 2 stats compiled")

remix = dub(track1Stats, track2Stats, track1.audio)
print("dub complete")
remix.write(r"C:\Users\jonathan\Desktop\output1.wav")
