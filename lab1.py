import random
import math
import matplotlib.pyplot as plot

def gen_u():
    return random.random()

def poisson_gen(lmbda):
    x = -1
    s = 1.0
    q = math.exp(-lmbda)

    while s > q:
        u = gen_u()
        s *= u
        x += 1

    return x

def normal_gen(mu, sigma):
    u1 = gen_u()
    u2 = gen_u()

    zero = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return mu + sigma * zero

def poisson_plot(poisson_data,lmbda):
    plot.figure()
    plot.hist(poisson_data, bins=range(max(poisson_data)+2), density=True)
    plot.title("Rozkład Poissona (lambda={})".format(lmbda))
    plot.xlabel("X")
    plot.ylabel("Częstość")
    plot.show()

def normal_gauss_plot(normal_data,bins_value,mu,sigma):
    plot.figure()
    plot.hist(normal_data, bins=bins_value, density=True)
    plot.title("Rozkład Normalny Gaussa (μ={}, σ={})".format(mu, sigma))
    plot.xlabel("X")
    plot.ylabel("Gęstość")
    plot.show()

def main():

    n = 10000
    seed = 91
    lmbda = 4
    mu = 0
    sigma = 1
    bins_value = 50

    if seed is not None:
        random.seed(seed)

    poisson_data = [poisson_gen(lmbda) for _ in range(n)]
    normal_data = [normal_gen(mu, sigma) for _ in range(n)]

    poisson_plot(poisson_data,lmbda)
    normal_gauss_plot(normal_data,bins_value,mu,sigma)


if __name__ == "__main__":
    main()
