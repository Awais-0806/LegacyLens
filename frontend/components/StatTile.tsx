import type { ReactNode } from "react";

type StatTileProps = {
  value: ReactNode;
  label: string;
};

export function StatTile({ value, label }: StatTileProps) {
  return (
    <div>
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
}
