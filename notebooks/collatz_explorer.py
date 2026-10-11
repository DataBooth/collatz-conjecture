import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import plotly.graph_objects as go
    from typing import List, Dict
    return Dict, List, go, mo


@app.cell
def _(Dict, List):
    class Collatz:
        """
        Generate, analyse, and visualise generalised Collatz sequences.

        Rules:
        - Even: n -> n / 2
        - Odd:  n -> n_factor * n + 1
        """

        def __init__(self, n_factor: int = 3) -> None:
            self.n_factor = n_factor
            self.sequences: Dict[int, List[int]] = {}
            self.metrics: Dict[int, Dict[str, int]] = {}

        def generate_sequence(self, start_number: int) -> List[int]:
            if start_number < 1:
                raise ValueError("Start number must be a positive integer.")

            n = start_number
            sequence = [n]

            # Safety limit to avoid infinite loops for non-standard factors
            max_steps = 10_000
            steps = 0

            while n != 1 and steps < max_steps:
                if n % 2 == 0:
                    n //= 2
                else:
                    n = self.n_factor * n + 1
                sequence.append(n)
                steps += 1

            self.sequences[start_number] = sequence
            self._calculate_metrics(start_number)
            return sequence

        def _calculate_metrics(self, start_number: int) -> None:
            sequence = self.sequences[start_number]
            self.metrics[start_number] = {
                "length": len(sequence),
                "max_value": max(sequence) if sequence else 0,
                "steps_to_one": max(0, len(sequence) - 1),
                "reached_one": sequence[-1] == 1 if sequence else False,
            }

        def get_metrics(self, start_number: int) -> Dict[str, int]:
            if start_number not in self.sequences:
                self.generate_sequence(start_number)
            return self.metrics[start_number]

        def clear(self) -> None:
            self.sequences.clear()
            self.metrics.clear()
    return (Collatz,)


@app.cell
def _(mo):
    mo.md(
        """
        # Collatz Conjecture Explorer

        Interactive exploration of **generalised Collatz sequences**.

        Classic rule (n_factor = 3):  
        - If even → divide by 2  
        - If odd → 3n + 1

        Change the multiplier, explore individual sequences, or compare many starting numbers at once.
        """
    )
    return


@app.cell
def _(mo):
    n_factor = mo.ui.slider(1, 15, value=3, label="Odd multiplier (n_factor)", show_value=True)
    start_range = mo.ui.slider(10, 200, value=50, label="Starting numbers to compare (1 to N)", show_value=True)
    common_origin = mo.ui.switch(value=False, label="Align sequences at step 0")
    single_start = mo.ui.number(value=27, start=1, stop=10000, label="Explore single starting number")
    return common_origin, n_factor, single_start, start_range


@app.cell
def _(common_origin, mo, n_factor, single_start, start_range):
    mo.hstack(
        [
            mo.vstack([n_factor, start_range]),
            mo.vstack([single_start, common_origin]),
        ],
        gap=2,
    )
    return


@app.cell
def _(Collatz, n_factor):
    collatz = Collatz(n_factor=n_factor.value)
    return (collatz,)


@app.cell
def _(collatz, mo, single_start):
    seq = collatz.generate_sequence(single_start.value)
    metrics = collatz.get_metrics(single_start.value)

    status = "✅ Reached 1" if metrics["reached_one"] else "⚠️ Did not reach 1 (hit step limit)"

    mo.vstack(
        [
            mo.md(f"### Sequence starting at **{single_start.value}**"),
            mo.md(f"**Status:** {status}  |  **Length:** {metrics['length']}  |  **Max value:** {metrics['max_value']:,}  |  **Steps to 1:** {metrics['steps_to_one']}"),
            mo.md(f"```\n{seq[:30]}{' ...' if len(seq) > 30 else ''}\n```"),
        ]
    )
    return metrics, seq


@app.cell
def _(collatz, common_origin, go, mo, start_range):
    starts = list(range(1, start_range.value + 1))

    fig = go.Figure()

    lengths = []
    maxes = []

    for s in starts:
        sequence = collatz.generate_sequence(s)
        m = collatz.get_metrics(s)
        lengths.append(m["length"])
        maxes.append(m["max_value"])

        if common_origin.value:
            x_vals = list(range(len(sequence)))
        else:
            x_vals = list(range(len(sequence)))

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=sequence,
                mode="lines",
                name=str(s),
                hovertemplate=f"Start {s}<br>Step: %{{x}}<br>Value: %{{y:,}}<extra></extra>",
                opacity=0.6,
            )
        )

    title = f"Generalised Collatz sequences (n_factor = {collatz.n_factor})"
    if common_origin.value:
        title += " — aligned at step 0"

    fig.update_layout(
        title=title,
        xaxis_title="Step",
        yaxis_title="Value",
        yaxis_type="log",
        height=520,
        showlegend=False,
        template="plotly_white",
        margin=dict(t=60, b=40),
    )

    mo.ui.plotly(fig)
    return fig, lengths, maxes


@app.cell
def _(go, lengths, maxes, mo, start_range):
    # Summary stats plot
    summary = go.Figure()

    summary.add_trace(
        go.Scatter(
            x=list(range(1, start_range.value + 1)),
            y=lengths,
            mode="markers+lines",
            name="Sequence length",
            yaxis="y1",
        )
    )

    summary.add_trace(
        go.Scatter(
            x=list(range(1, start_range.value + 1)),
            y=maxes,
            mode="markers",
            name="Max value",
            yaxis="y2",
            marker=dict(size=6, opacity=0.7),
        )
    )

    summary.update_layout(
        title="Sequence length and peak value by starting number",
        xaxis_title="Starting number",
        yaxis=dict(title="Length", side="left"),
        yaxis2=dict(title="Max value", side="right", overlaying="y", type="log"),
        height=400,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    mo.ui.plotly(summary)
    return


@app.cell
def _(mo):
    mo.md(
        """
        ---
        **Notes**

        - The classic Collatz conjecture claims every positive integer eventually reaches 1 under the 3n+1 rule. It remains unproven.
        - For n_factor ≠ 3 the behaviour can diverge or cycle; a step limit (10,000) is applied to keep the explorer responsive.
        - Toggle “Align sequences at step 0” to compare trajectory shapes rather than absolute position.
        """
    )
    return


if __name__ == "__main__":
    app.run()
