import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILLS_DIR = path.join(__dirname, '../skills');

/**
 * 递归读取目录下所有文件
 */
function readDirRecursive(dir) {
  const result = {};

  if (!fs.existsSync(dir)) {
    return result;
  }

  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      result[item] = readDirRecursive(fullPath);
    } else {
      result[item] = fs.readFileSync(fullPath, 'utf-8');
    }
  }

  return result;
}

/**
 * 解析单个技能
 */
function parseSkill(skillDir) {
  const skillPath = path.join(SKILLS_DIR, skillDir);

  // 检查 SKILL.md 是否存在
  if (!fs.existsSync(path.join(skillPath, 'SKILL.md'))) {
    console.warn(`Skip ${skillDir}: no SKILL.md`);
    return null;
  }

  // 读取所有文件
  const files = readDirRecursive(skillPath);

  // 从 SKILL.md 提取元数据
  let metadata = {
    name: skillDir,
    displayName: skillDir,
    description: '',
    author: 'ulanzi',
    version: '1.0.0',
    tags: [],
    platforms: ['claude-code', 'openclaw']
  };

  const skillMd = files['SKILL.md'] || '';

  // 解析 YAML frontmatter
  const frontmatterMatch = skillMd.match(/^---([\s\S]*?)---/m);
  if (frontmatterMatch) {
    const lines = frontmatterMatch[1].split('\n');
    for (const line of lines) {
      const colonIndex = line.indexOf(':');
      if (colonIndex === -1) continue;
      const key = line.slice(0, colonIndex).trim();
      const value = line.slice(colonIndex + 1).trim();

      if (key === 'name') metadata.name = value;
      if (key === 'description') metadata.description = value;
      if (key === 'version') metadata.version = value;
      if (key === 'author') metadata.author = value;
      if (key === 'tags') {
        metadata.tags = value.replace(/[\[\]]/g, '').split(',').map(t => t.trim()).filter(t => t);
      }
    }

    // 设置 displayName
    metadata.displayName = metadata.name
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  return {
    id: `ulanzi/${metadata.name}`,
    ...metadata,
    files
  };
}

/**
 * 生成 skills.json
 */
function generateSkillsJson() {
  console.log('🔍 Scanning skills directory...\n');

  if (!fs.existsSync(SKILLS_DIR)) {
    console.error('❌ skills directory not found');
    process.exit(1);
  }

  const skillDirs = fs.readdirSync(SKILLS_DIR)
    .filter(dir => {
      const skillPath = path.join(SKILLS_DIR, dir);
      return fs.statSync(skillPath).isDirectory();
    });

  console.log(`📁 Found ${skillDirs.length} skills\n`);

  const skills = [];

  for (const dir of skillDirs) {
    const skill = parseSkill(dir);
    if (skill) {
      skills.push(skill);
      console.log(`✅ ${skill.displayName} (${skill.id})`);
    }
  }

  const packageJson = JSON.parse(
    fs.readFileSync(path.join(__dirname, '../package.json'), 'utf-8')
  );

  const output = {
    version: packageJson.version || '1.0.0',
    generatedAt: new Date().toISOString(),
    source: {
      type: 'npm',
      name: packageJson.name,
      registry: 'https://registry.npmjs.org',
      repository: packageJson.repository?.url?.replace('git+', '').replace('.git', '') || ''
    },
    skills
  };

  fs.writeFileSync(
    path.join(__dirname, '../skills.json'),
    JSON.stringify(output, null, 2)
  );

  console.log(`\n🎉 Generated skills.json with ${skills.length} skills`);
}

generateSkillsJson();
