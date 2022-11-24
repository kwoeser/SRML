import statistics as stats

def print_stats(filename: str):
    with open(filename, 'r') as f:
        data = f.read()
        data = [float(x) for x in data.split()]
    print(('{:>10}' * 4).format('min', 'max', 'mean', 'median'))
    print(('{:>10.2f}' * 4).format(min(data), max (data), stats.mean (data), 
stats

.median(data)))

if 
__name__

 == '__main__':
    print_stats('data.txt')
