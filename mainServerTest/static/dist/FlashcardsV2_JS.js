// Your App component
class App extends React.Component {
  constructor() {
    super();
    this.state = {
      cards: [
        { front: "1. What is the main concept discussed in the text?", back: "- The main concept discussed in the text is the importance of artificial intelligence in advancing various industries and sectors." },
        { front: "2. How does the text explain the role of machine learning in the context of artificial intelligence?", back: "- The text explains that machine learning is a subfield of artificial intelligence that involves the development of algorithms and models that allow computers to learn from data and make predictions or decisions." },
        // Add more cards as needed
      ]
    };
  }

  render() {
    return (
      <div className="App">
        <Flashcards cards={this.state.cards} />
      </div>
    );
  }
}

// Render the App component
ReactDOM.render(<App />, document.getElementById('flashcard-view'));
