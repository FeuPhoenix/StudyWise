// Define the Flashcards component
class Flashcards extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      cardIndex: 0
    };
  }

  arrowHandler = (left) => {
    const { cardIndex } = this.state;
    if (left) {
      if (cardIndex - 1 >= 0) {
        this.setState({ cardIndex: cardIndex - 1 });
      }
    } else {
      if (cardIndex + 1 < this.props.cards.length) {
        this.setState({ cardIndex: cardIndex + 1 });
      }
    }
  };

  render() {
    return (
      <div className="flashcard-viewer noselect">
        <div className="flashcard-item-wrapper">
          <Flashcard card={this.props.cards[this.state.cardIndex]} />
        </div>
        <div>
          <NavButtons
            arrowHandler={this.arrowHandler}
            cardIndex={this.state.cardIndex}
            cardLength={this.props.cards.length}
          />
        </div>
      </div>
    );
  }
}
