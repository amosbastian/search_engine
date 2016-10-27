from wordcloud import WordCloud
import os

def create_cloud(text, filename):
    try:
        if os.name == "nt":
            static = os.path.realpath("..") + "\static\images\\"
        else:
            static = os.path.realpath("..") + "/static/"

        wordcloud = WordCloud(max_font_size=40).generate(text)

        import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig("{}{}.png".format(static, filename), transparent=True)
        plt.close("all")
    except(IndexError):
        return

if __name__ == '__main__':
    text = "My name is Amos Bastian and this is an example image"
    create_cloud(text, "test123")