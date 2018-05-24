from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
from time import time

TEST_RESULTS = ['link1', 'link2', 'link3', 'link4', 'link5555555555555555555555555555555555555']

class Link(Label):
    def __init__(self, rank:int, link:str):
        super(Link, self).__init__()
        self.text_size[0] = Window.size[0]
        self.padding_x = 20
        self.halign = 'left'
        self.valign = 'middle'
        self.text = "{}     {}".format(str(rank), link)

class SearchBar(BoxLayout):
    def __init__(self, **kwargs):
        super(SearchBar, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.button = Button(text='Search', font_size=25, size_hint=(0.4,1))
        self.query = TextInput(multiline=False, font_size=20)

        self.add_widget(self.query)
        self.add_widget(self.button)


class GuiLayout(GridLayout):
    def __init__(self, **kwargs):
        super(GuiLayout, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 13
        self.timeLabel = Label(text='Time to Search: None')
        self.links = []

        #Binding Search Button to run Search Engine
        self.searchBar = SearchBar()
        self.searchBar.button.bind(on_press=self.runSearchEngine)

        self.add_widget(Label(text='ICS Mini Search Engine', font_size=25))
        self.add_widget(self.searchBar)
        self.add_widget(self.timeLabel)
        self.add_links(TEST_RESULTS)

        Window.bind(on_resize=self.update_link_text_size)

    def reset_links(self):
        for link in self.links:
            self.remove_widget(link)

    def update_link_text_size(self, instance1, instance2, instance3):
        for link in self.links:
            link.text_size[0] = Window.size[0]

    def add_links(self, linksList: [str]):
        #If there are less than 10 links, fill list up with None
        while len(linksList) < 10:
            linksList.append(None)

        for n,link in enumerate(linksList):
            if link == None:
                linkWidget = Link(n+1, "No Link"); self.add_widget(linkWidget)
            else:
                linkWidget = Link(n+1, link); self.add_widget(linkWidget)
            self.links.append(linkWidget)

    def runSearchEngine(self, instance):
        start = time()
        print('Beginning to run Search Engine...')
        query = self.searchBar.query.text
        print(query)

        #Search Output Links Here / Query search code should be under here
        linkResults = [] # result have query search
        self.reset_links()
        self.add_links(linkResults)

        self.timeLabel.text = "Time to Search: {} seconds".format(round(start - time(),2))


class SearchEngineGui(App):
    def build(self):
        return GuiLayout()

if __name__ == '__main__':
    SearchEngineGui().run()