class Configs:
    def __init__(self):
        self.output_dir = 'build'
        self.input_dir = '.'
        self.templates_dir = 'templates'
        self.rss_feed_path = 'rss.xml'


class Spybg:
    def __init__(self):
        self.configs = Configs()

    def generate(self):
        pass


def main():
    spybg = Spybg()
    spybg.generate()


if __name__ == "main":
    main()