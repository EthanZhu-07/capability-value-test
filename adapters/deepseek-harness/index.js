import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

export const name = 'capability-value-test'
export const inject = ['skills']

const adapterDirectory = dirname(fileURLToPath(import.meta.url))
const packageRoot = resolve(adapterDirectory, '..', '..')
const skillPath = resolve(packageRoot, 'SKILL.md')

function splitFrontmatter(raw) {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/u)
  if (match === null) {
    throw new Error('SKILL.md must contain YAML frontmatter')
  }
  return { frontmatter: match[1], content: match[2].trim() }
}

function parseScalar(frontmatter, key) {
  const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/gu, '\\$&')
  const match = frontmatter.match(new RegExp(`^${escapedKey}:\\s*(.+)$`, 'mu'))
  if (match === null) return undefined

  const value = match[1].trim()
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1)
  }
  return value
}

export function loadBundledSkill() {
  const { frontmatter, content } = splitFrontmatter(readFileSync(skillPath, 'utf8'))
  const skillName = parseScalar(frontmatter, 'name')
  const description = parseScalar(frontmatter, 'description')

  if (skillName === undefined || description === undefined || content === '') {
    throw new Error('SKILL.md requires non-empty name, description, and body')
  }

  return {
    name: skillName,
    description,
    content,
    source: 'bundled',
    path: skillPath,
    resourceBase: { kind: 'directory', path: packageRoot },
  }
}

export function apply(ctx) {
  return ctx.skills.register(loadBundledSkill())
}
