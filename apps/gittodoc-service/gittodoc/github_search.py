import os, requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN","")

def gh_headers():
  h={"Accept":"application/vnd.github+json"}
  if GITHUB_TOKEN: h["Authorization"]=f"Bearer {GITHUB_TOKEN}"
  return h

def search_repos(q: str, per_page=5):
  url="https://api.github.com/search/repositories"
  r=requests.get(url, params={"q":q,"per_page":per_page}, headers=gh_headers(), timeout=15)
  r.raise_for_status()
  return r.json()

def search_code(q: str, repo: str, per_page=5):
  url="https://api.github.com/search/code"
  r=requests.get(url, params={"q":f"{q} repo:{repo}","per_page":per_page}, headers=gh_headers(), timeout=15)
  r.raise_for_status()
  return r.json()
