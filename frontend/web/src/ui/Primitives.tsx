import React from "react";

export function Card({ children }: { children: React.ReactNode }) {
  return <div className="card">{children}</div>;
}

export function PrimaryButton(
  props: React.ButtonHTMLAttributes<HTMLButtonElement> & { children: React.ReactNode },
) {
  return <button {...props} className={`primaryBtn ${props.className ?? ""}`.trim()} />;
}

export function Field({
  label,
  value,
  onChange,
  type = "text",
  autoComplete,
  hint,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  autoComplete?: string;
  hint?: string;
}) {
  return (
    <label className="field">
      <div className="fieldLabel">
        <span>{label}</span>
        {hint ? <span className="fieldHint">{hint}</span> : null}
      </div>
      <input
        className="input"
        type={type}
        value={value}
        autoComplete={autoComplete}
        onChange={(e) => onChange(e.target.value)}
        required
      />
    </label>
  );
}

