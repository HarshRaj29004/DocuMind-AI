function SourceCitations({ citations }) {
  return (
    <section className="panel">
      <h2>Source Citations</h2>
      {citations.length === 0 ? (
        <p className="muted">Citations will appear after you ask a question.</p>
      ) : (
        <ul className="citations-list">
          {citations.map((citation) => (
            <li key={citation.id}>
              <header>
                <strong>{citation.source}</strong>
                <span>score: {citation.score}</span>
              </header>
              <p>{citation.text}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default SourceCitations
