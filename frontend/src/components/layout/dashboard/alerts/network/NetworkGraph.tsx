import CytoscapeComponent from "react-cytoscapejs";
import type { StylesheetJsonBlock } from "cytoscape";
import { mockNetwork } from "../../../../../mocks/data";

export default function NetworkGraph() {
  const elements = [
    ...mockNetwork.nodes.map((node) => ({
      data: {
        id: node.id,
        label: `${node.label}\nRisk: ${node.risk_score}`,
        risk_score: node.risk_score,
      },
    })),

    ...mockNetwork.edges.map((edge) => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        weight: edge.weight,
      },
    })),
  ];

  const stylesheet = [
    {
      selector: "node",
      style: {
        "background-color": "#2563eb",
        label: "data(label)",
        color: "#ffffff",
        "font-size": "10px",
        "text-valign": "center",
        "text-halign": "center",
        width: "45px",
        height: "45px",
        "border-width": 2,
        "border-color": "#60a5fa",
      },
    },
    {
      selector: "node[risk_score >= 80]",
      style: {
        "background-color": "#dc2626",
        "border-color": "#f87171",
      },
    },
    {
      selector: "node[risk_score >= 60][risk_score < 80]",
      style: {
        "background-color": "#f97316",
        "border-color": "#fb923c",
      },
    },
    {
      selector: "node[risk_score < 40]",
      style: {
        "background-color": "#16a34a",
        "border-color": "#4ade80",
      },
    },
    {
      selector: "edge",
      style: {
        width: "data(weight)",
        "line-color": "#475569",
        "target-arrow-color": "#475569",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
      },
    },
    {
      selector: "node:selected",
      style: {
        "border-width": 4,
        "border-color": "#ffffff",
      },
    },
  ] as StylesheetJsonBlock[];

  return (
    <div className="h-[600px] w-full overflow-hidden rounded-lg border border-gray-800 bg-[#0b1016]">
      <CytoscapeComponent
        elements={elements}
        stylesheet={stylesheet as any}
        style={{ width: "100%", height: "100%" }}
        layout={{
          name: "cose",
          animate: true,
          fit: true,
          padding: 50,
        }}
      />
    </div>
  );
}