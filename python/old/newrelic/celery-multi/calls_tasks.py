import tasks


def main():
    for _ in xrange(3):
        print 'slowly...'
        tasks.slowly.delay(1)


if __name__ == '__main__':
    main()
