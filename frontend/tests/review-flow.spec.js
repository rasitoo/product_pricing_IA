import { describe, expect, it } from "vitest";

import { canExport } from "../src/state/reviewState.js";

describe("review flow", () => {
  it("allows export only when approved", () => {
    expect(canExport("approved")).toBe(true);
    expect(canExport("rejected")).toBe(false);
  });
});
