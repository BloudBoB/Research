cat > ./test.yaml << EOF
apiVersion: 2019-12-01
location: koreacentral
name: pocContainergroup
properties:
  osType: linux
  containers:
  - name: c1
    properties:
      image: runjivu/hubrepo:5736
      resources:
        requests:
          cpu: 2
          memoryInGb: 6
$(for i in {2..5}; do
cat << EOC
  - name: c$i
    properties:
      image: runjivu/hubrepo:ubuntubase
      command: ["/bin/sleep","inf"]
      resources:
        requests:
          cpu: 0.1
          memoryInGB: 0.5
        limits:
          cpu: 0.1
          memoryInGb: 0.6
EOC
EOF