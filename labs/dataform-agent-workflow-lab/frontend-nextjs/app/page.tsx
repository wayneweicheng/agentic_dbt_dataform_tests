export default function Home() {
  return (
    <main style={{ padding: 32, fontFamily: "sans-serif" }}>
      <h1>Dataform Agent Workflow Lab</h1>
      <p>Use this page as the browser entry point for the workflow trigger app.</p>
      <form action="/api/run-workflow" method="post">
        <button type="submit">Run workflow</button>
      </form>
    </main>
  );
}
