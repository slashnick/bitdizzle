"use strict";

function createJournalEntry(newEntry) {
  fetch("/entries/", {
    method: "POST",
    body: JSON.stringify(newEntry),
    headers: {
      "Content-Type": "application/json",
    },
  });
}

function deleteAllEntries() {
  fetch("/entries/", { method: "DELETE" }).then(
    () => (window.location = window.location)
  );
}

class Journal extends React.PureComponent {
  constructor(props) {
    super(props);
    this.state = { entries: [] };
  }

  addJournalEntry(newEntry) {
    this.setState({ entries: [newEntry, ...this.state.entries] });
    createJournalEntry(newEntry);
  }

  render() {
    const entries = [...this.state.entries, ...this.props.entries];
    return React.createElement(
      "div",
      { className: "Journal" },
      React.createElement(NewEntryForm, {
        onSubmit: this.addJournalEntry.bind(this),
      }),
      entries.map((entry, i) =>
        React.createElement(JournalEntry, {
          ...entry,
          key: entries.length - i - 1,
        })
      ),
      React.createElement(DeleteAllEntriesButton)
    );
  }
}

class NewEntryForm extends React.PureComponent {
  constructor(props) {
    super(props);
    this.state = { title: "", body: "" };
  }

  onTitleChange(event) {
    this.setState({ title: event.target.value });
  }

  onBodyChange(event) {
    event.target.style.height = "auto";
    event.target.style.height = event.target.scrollHeight + "px";
    this.setState({ body: event.target.value });
  }

  onSubmit(event) {
    event.preventDefault();
    const entry = { title: this.state.title, body: this.state.body };
    this.setState({ title: "", body: "" });
    this.props.onSubmit(entry);
  }

  render() {
    const me = this;
    return React.createElement(
      "form",
      {
        className: "NewEntryForm",
        onSubmit: this.onSubmit.bind(this),
      },
      React.createElement("input", {
        className: "NewEntryForm-title",
        placeholder: "New private journal entry",
        autoFocus: true,
        value: this.state.title,
        onChange: this.onTitleChange.bind(this),
      }),
      React.createElement("textarea", {
        className: "NewEntryForm-body",
        placeholder: "Today, the funniest thing happened...",
        value: this.state.body,
        onChange: this.onBodyChange.bind(this),
      }),
      React.createElement("input", {
        className: "NewEntryForm-save",
        type: "submit",
        value: "Save",
      })
    );
  }
}

const JournalEntry = (props) =>
  React.createElement(
    "div",
    { className: "JournalEntry" },
    React.createElement(
      "div",
      { className: "JournalEntry-title" },
      props.title
    ),
    React.createElement("div", { className: "JournalEntry-body" }, props.body)
  );

const DeleteAllEntriesButton = (props) =>
  React.createElement(
    "button",
    {
      className: "DeleteAllEntriesButton",
      onClick: () => {
        if (
          confirm("Delete all your journal entries? This cannot be undone.")
        ) {
          deleteAllEntries();
        }
      },
    },
    "Delete all journal entries"
  );

ReactDOM.createRoot(document.getElementById("root")).render(
  React.createElement(Journal, window.initialProps || { entries: [] })
);
