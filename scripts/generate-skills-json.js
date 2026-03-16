import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILLS_DIR = path.join(__dirname, '../skills');

/**
 * 读取目录下的所有文件
 */
function readDirRecursive(dir, basePath = '') {
  const result = {};

  if (!fs.existsSync(dir)) {
    return result;
  }

  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const relativePath = basePath ? `${basePath}/${item}` : item;
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      result[item] = readDirRecursive(fullPath, relativePath);
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
    console.warn(`⚠️  ${skillDir}: 缺少 SKILL.md，跳过`);
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
  const frontmatterMatch = skillMd.match(/^---
([\s\S]*?)\n---/);
  if (frontmatterMatch) {
    const frontmatter = frontmatterMatch[1];

    const nameMatch = frontmatter.match(/name:\s*(.+)/);
    const descMatch = frontmatter.match(/description:\s*(.+)/);
    const versionMatch = frontmatter.match(/version:\s*(.+)/);
    const authorMatch = frontmatter.match(/author:\s*(.+)/);
    const tagsMatch = frontmatter.match(/tags:\s*\[(.*)\]/);
    const platformsMatch = frontmatter.match(/platforms:\s*\n\s*-\s*(.+)/g);

    if (nameMatch) metadata.name = nameMatch[1].trim();
    if (descMatch) metadata.description = descMatch[1].trim();
    if (versionMatch) metadata.version = versionMatch[1].trim();
    if (authorMatch) metadata.author = authorMatch[1].trim();
    if (tagsMatch) {
      metadata.tags = tagsMatch[1].split(',').map(t => t.trim());
    }
    if (platformsMatch) {
      metadata.platforms = platformsMatch.map(p => p.replace(/platforms:\s*\n\s*-\s*/, '').trim());
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
  console.log('🔍 扫描 skills 目录...\n');

  if (!fs.existsSync(SKILLS_DIR)) {
    console.error('❌ skills 目录不存在');
    process.exit(1);
  }

  const skillDirs = fs.readdirSync(SKILLS_DIR)
    .filter(dir => {
      const skillPath = path.join(SKILLS_DIR, dir);
      return fs.statSync(skillPath).isDirectory();
    });

  console.log(`📁 找到 ${skillDirs.length} 个技能目录\n`);

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

  console.log(`\n🎉 已生成 skills.json，包含 ${skills.length} 个技能`);
}

generateSkillsJson();
