import Link from 'next/link';

const stats = [
  { title: 'Active Tasks', value: '5' },
  { title: 'Workflows', value: '12' },
  { title: 'Connected Browsers', value: '3' },
];

export default function DashboardPage() {
  return (
    <div className="min-h-screen px-6 py-8">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-semibold">KeyaZ Agent</h1>
          <p className="text-slate-400 mt-2">Autonomous browser automation and agent monitoring.</p>
        </div>
        <Link href="/settings" className="rounded-full bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-400">
          Settings
        </Link>
      </div>

      <section className="grid gap-4 sm:grid-cols-3 mb-8">
        {stats.map((stat) => (
          <div key={stat.title} className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-lg shadow-slate-950/20">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">{stat.title}</p>
            <p className="mt-4 text-3xl font-semibold">{stat.value}</p>
          </div>
        ))}
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-lg shadow-slate-950/20">
          <div className="flex items-center justify-between gap-4 mb-4">
            <div>
              <h2 className="text-xl font-semibold">Create a new task</h2>
              <p className="text-slate-400">Start a browser automation workflow with your prompt.</p>
            </div>
          </div>
          <form className="space-y-4">
            <div>
              <label className="text-sm text-slate-500">Prompt</label>
              <textarea className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-100 focus:border-sky-500 focus:outline-none" rows={4} placeholder="Ask the agent to log in, navigate, or scrape data..."></textarea>
            </div>
            <button type="submit" className="inline-flex items-center justify-center rounded-full bg-sky-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-sky-400">
              Launch Task
            </button>
          </form>
        </section>

        <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-lg shadow-slate-950/20">
          <h2 className="text-xl font-semibold mb-3">Recent tasks</h2>
          <div className="space-y-3">
            {['Draft login sequence', 'Check pricing page', 'Book demo meeting'].map((task, index) => (
              <div key={index} className="rounded-3xl border border-slate-800 bg-slate-950 p-4">
                <div className="flex items-center justify-between gap-2">
                  <p className="font-medium text-slate-100">{task}</p>
                  <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase tracking-[0.18em] text-slate-400">running</span>
                </div>
                <div className="mt-3 flex items-center justify-between gap-3 text-sm text-slate-400">
                  <p>Started 3m ago</p>
                  <Link href="/tasks/123" className="text-sky-400 hover:text-sky-300">
                    Watch Live
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
